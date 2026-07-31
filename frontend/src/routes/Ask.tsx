export default function Ask() {
  return (
    <div className="flex justify-center">
      <div className="mx-10 md:mx-0 md:w-175 flex flex-col gap-4 text-justify">
        <div>
          <h2 className="page-title text-xl">Ask Canary a question</h2>
        </div>
        <div className="flex flex-col gap-y-5">
          <p>
            The alpha testing version supports a limited selection of analysis.
            These examples are representative of what the agent can handle:
          </p>
          <ul className="flex flex-col gap-y-2 list-disc">
            <li>
              Give me Apple's closing share price from January to March 2026
            </li>
            <li>
              Show me the daily returns on Apple's stock price as well as the
              volatility of this over a 5-day window in January 2026
            </li>
            <li>
              Compare the opening prices of Apple, Google, Microsoft, Nvidia,
              Tesla, JP Morgan, and Bank of America from January to March 2026.
              I want to use an index from the beginning.
            </li>
            <li>
              Break down the market capitalisation of all public companies by
              sector, industry, then company, and show it in a treemap. Also
              show the share price of each company.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
